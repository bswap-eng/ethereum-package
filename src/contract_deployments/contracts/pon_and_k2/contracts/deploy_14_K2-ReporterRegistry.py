from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
import os
import time
import logging

# Account Alias: PON
ACCOUNT_ALIAS = "PON"

# ReporterRegistry contract bytecode
BYTE_CODE = "0x60a06040523060805234801561001457600080fd5b5061001d610022565b6100e1565b600054610100900460ff161561008e5760405162461bcd60e51b815260206004820152602760248201527f496e697469616c697a61626c653a20636f6e747261637420697320696e697469604482015266616c697a696e6760c81b606482015260840160405180910390fd5b60005460ff908116146100df576000805460ff191660ff9081179091556040519081527f7f26b83ff96e1f2b6a682f133852f6798a09c465da95921460cefb38474024989060200160405180910390a15b565b6080516124ed620001196000396000818161060b0152818161064b015281816106ea0152818161072a01526107bd01526124ed6000f3fe60806040526004361061012a5760003560e01c80637fadd755116100ab578063965336d81161006f578063965336d8146103675780639e9de9091461037c578063a18c63aa146103b8578063b6abbb50146103d9578063e6afef17146103f9578063f2fde38b1461041957600080fd5b80637fadd7551461029c57806383612af9146102cd57806384b0196e146102ed5780638da5cb5b14610315578063906571471461034757600080fd5b80634f1ef286116100f25780634f1ef2861461020e57806352d1902d146102215780635e65db2314610236578063654521f014610256578063715018a61461028757600080fd5b806305d5b9821461012f5780632468fe9e1461016257806330a63c9f146101a35780633659cfe6146101ba5780634a882fc3146101da575b600080fd5b34801561013b57600080fd5b5061014f61014a366004611aa7565b610439565b6040519081526020015b60405180910390f35b34801561016e57600080fd5b5061019361017d366004611adc565b6101326020526000908152604090205460ff1681565b6040519015158152602001610159565b3480156101af57600080fd5b506101b86104e7565b005b3480156101c657600080fd5b506101b86101d5366004611b0a565b610601565b3480156101e657600080fd5b5061014f7f4352fc3864fd6f94dbf2b42d0b365813b8c24532ae2fefa68d2993e095be585c81565b6101b861021c366004611bfe565b6106e0565b34801561022d57600080fd5b5061014f6107b0565b34801561024257600080fd5b50610193610251366004611b0a565b610863565b34801561026257600080fd5b50610193610271366004611b0a565b6101306020526000908152604090205460ff1681565b34801561029357600080fd5b506101b86108ac565b3480156102a857600080fd5b506101936102b7366004611b0a565b6101316020526000908152604090205460ff1681565b3480156102d957600080fd5b506101b86102e8366004611c62565b6108c0565b3480156102f957600080fd5b50610302610ab6565b6040516101599796959493929190611d0c565b34801561032157600080fd5b506033546001600160a01b03165b6040516001600160a01b039091168152602001610159565b34801561035357600080fd5b506101b8610362366004611dc2565b610b54565b34801561037357600080fd5b506101b8610c9e565b34801561038857600080fd5b50610193610397366004611e38565b61013360209081526000928352604080842090915290825290205460ff1681565b3480156103c457600080fd5b5061012f5461032f906001600160a01b031681565b3480156103e557600080fd5b506101936103f4366004611c62565b610d49565b34801561040557600080fd5b506101b8610414366004611e64565b610e40565b34801561042557600080fd5b506101b8610434366004611b0a565b610f32565b6000807f4352fc3864fd6f94dbf2b42d0b365813b8c24532ae2fefa68d2993e095be585c61046a6020850185611f2c565b61047a6040860160208701611b0a565b60408601356060870135608088013561049660a08a018a611f4d565b6040516104a4929190611f9b565b6040519081900381206104bf97969594939291602001611fe3565b6040516020818303038152906040528051906020012090506104e081610fa8565b9392505050565b336000818152610130602052604090205460ff161561054d5760405162461bcd60e51b815260206004820152601b60248201527f5265706f7274657220616c72656164792072656769737465726564000000000060448201526064015b60405180910390fd5b6001600160a01b0381163b156105a55760405162461bcd60e51b815260206004820152601d60248201527f436f6e7472616374732063616e6e6f74206265207265706f72746572730000006044820152606401610544565b6001600160a01b03811660008181526101306020908152604091829020805460ff1916600117905590519182527ff761f8e41ce3e566cee51d2a2197e8db130cfaf8e33c0d88621dbe6cdef7e4b491015b60405180910390a150565b6001600160a01b037f00000000000000000000000000000000000000000000000000000000000000001630036106495760405162461bcd60e51b815260040161054490612029565b7f00000000000000000000000000000000000000000000000000000000000000006001600160a01b0316610692600080516020612471833981519152546001600160a01b031690565b6001600160a01b0316146106b85760405162461bcd60e51b815260040161054490612075565b6106c181610fd5565b604080516000808252602082019092526106dd91839190610fdd565b50565b6001600160a01b037f00000000000000000000000000000000000000000000000000000000000000001630036107285760405162461bcd60e51b815260040161054490612029565b7f00000000000000000000000000000000000000000000000000000000000000006001600160a01b0316610771600080516020612471833981519152546001600160a01b031690565b6001600160a01b0316146107975760405162461bcd60e51b815260040161054490612075565b6107a082610fd5565b6107ac82826001610fdd565b5050565b6000306001600160a01b037f000000000000000000000000000000000000000000000000000000000000000016146108505760405162461bcd60e51b815260206004820152603860248201527f555550535570677261646561626c653a206d757374206e6f742062652063616c60448201527f6c6564207468726f7567682064656c656761746563616c6c00000000000000006064820152608401610544565b5060008051602061247183398151915290565b6001600160a01b0381166000908152610130602052604081205460ff1680156108a657506001600160a01b0382166000908152610131602052604090205460ff16155b92915050565b6108b461114d565b6108be60006111a7565b565b6108c86111f9565b336108d281610863565b61091e5760405162461bcd60e51b815260206004820152601860248201527f5265706f72746572206e6f6e2d6f7065726174696f6e616c00000000000000006044820152606401610544565b6109288383610d49565b6109745760405162461bcd60e51b815260206004820152601860248201527f5265706f7274207369676e617475726520696e76616c696400000000000000006044820152606401610544565b6001610133600061098b6040870160208801611b0a565b6001600160a01b0390811682526020808301939093526040918201600090812060608901358252845291909120805460ff19169315159390931790925561012f549091169063b87f3096906109e290860186611f2c565b6109f26040870160208801611b0a565b8660400135856040518563ffffffff1660e01b8152600401610a1794939291906120c1565b600060405180830381600087803b158015610a3157600080fd5b505af1158015610a45573d6000803e3d6000fd5b505050507fe454e2a62061933467f0642e772a8e280b5cc74107a8edb2a77999955395f99f81846020016020810190610a7e9190611b0a565b604080516001600160a01b039384168152929091166020830152808601359082015260600160405180910390a1506107ac6001609955565b6000606080600080600060606065546000801b148015610ad65750606654155b610b1a5760405162461bcd60e51b81526020600482015260156024820152741152540dcc4c8e88155b9a5b9a5d1a585b1a5e9959605a1b6044820152606401610544565b610b22611259565b610b2a6112eb565b60408051600080825260208201909252600f60f81b9b939a50919850469750309650945092509050565b600054610100900460ff1615808015610b745750600054600160ff909116105b80610b8e5750303b158015610b8e575060005460ff166001145b610bf15760405162461bcd60e51b815260206004820152602e60248201527f496e697469616c697a61626c653a20636f6e747261637420697320616c72656160448201526d191e481a5b9a5d1a585b1a5e995960921b6064820152608401610544565b6000805460ff191660011790558015610c14576000805461ff0019166101001790555b610c1c6112fa565b610c268383611329565b610c2e61135a565b610c36611389565b61012f80546001600160a01b0319166001600160a01b0386161790558015610c98576000805461ff0019169055604051600181527f7f26b83ff96e1f2b6a682f133852f6798a09c465da95921460cefb38474024989060200160405180910390a15b50505050565b33610ca881610863565b610cf45760405162461bcd60e51b815260206004820152601860248201527f5265706f72746572206e6f74206f7065726174696f6e616c00000000000000006044820152606401610544565b6001600160a01b03811660009081526101316020908152604091829020805460ff1916600117905590513381527fb43a381900658be21a4ed742c88a5254017f033cd3fe1aca72a3ba9c3123e2c191016105f6565b60008260800135431115610d895760405162461bcd60e51b8152602060048201526007602482015266115e1c1a5c995960ca1b6044820152606401610544565b6101336000610d9e6040860160208701611b0a565b6001600160a01b03168152602080820192909252604090810160009081206060870135825290925290205460ff1615610e115760405162461bcd60e51b815260206004820152601560248201527414db1bdd08185b1c9958591e481c995c1bdc9d1959605a1b6044820152606401610544565b6000610e1c84610439565b9050610e38610e316040860160208701611b0a565b84836113b0565b949350505050565b8280610e7c5760405162461bcd60e51b815260206004820152600b60248201526a456d70747920617272617960a81b6044820152606401610544565b808214610ecb5760405162461bcd60e51b815260206004820152601960248201527f496e636f6e73697374656e74206172726179206c656e677468000000000000006044820152606401610544565b60005b81811015610f2a57610f1a868683818110610eeb57610eeb6120f7565b9050602002810190610efd919061210d565b858584818110610f0f57610f0f6120f7565b9050606002016108c0565b610f238161212d565b9050610ece565b505050505050565b610f3a61114d565b6001600160a01b038116610f9f5760405162461bcd60e51b815260206004820152602660248201527f4f776e61626c653a206e6577206f776e657220697320746865207a65726f206160448201526564647265737360d01b6064820152608401610544565b6106dd816111a7565b60006108a6610fb561146a565b8360405161190160f01b8152600281019290925260228201526042902090565b6106dd61114d565b7f4910fdfa16fed3260ed0e7147f7cc6da11a60208b5b9406d12a635614ffd91435460ff16156110155761101083611479565b505050565b826001600160a01b03166352d1902d6040518163ffffffff1660e01b8152600401602060405180830381865afa92505050801561106f575060408051601f3d908101601f1916820190925261106c91810190612154565b60015b6110d25760405162461bcd60e51b815260206004820152602e60248201527f45524331393637557067726164653a206e657720696d706c656d656e7461746960448201526d6f6e206973206e6f74205555505360901b6064820152608401610544565b60008051602061247183398151915281146111415760405162461bcd60e51b815260206004820152602960248201527f45524331393637557067726164653a20756e737570706f727465642070726f786044820152681a58589b195555525160ba1b6064820152608401610544565b50611010838383611515565b6033546001600160a01b031633146108be5760405162461bcd60e51b815260206004820181905260248201527f4f776e61626c653a2063616c6c6572206973206e6f7420746865206f776e65726044820152606401610544565b603380546001600160a01b038381166001600160a01b0319831681179093556040519116919082907f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e090600090a35050565b60026099540361124b5760405162461bcd60e51b815260206004820152601f60248201527f5265656e7472616e637947756172643a207265656e7472616e742063616c6c006044820152606401610544565b6002609955565b6001609955565b6060606780546112689061216d565b80601f01602080910402602001604051908101604052809291908181526020018280546112949061216d565b80156112e15780601f106112b6576101008083540402835291602001916112e1565b820191906000526020600020905b8154815290600101906020018083116112c457829003601f168201915b5050505050905090565b6060606880546112689061216d565b600054610100900460ff166113215760405162461bcd60e51b8152600401610544906121a1565b6108be61153a565b600054610100900460ff166113505760405162461bcd60e51b8152600401610544906121a1565b6107ac828261156a565b600054610100900460ff166113815760405162461bcd60e51b8152600401610544906121a1565b6108be6115b9565b600054610100900460ff166108be5760405162461bcd60e51b8152600401610544906121a1565b6000806113d3836113c460208701876121ec565b866020013587604001356115e0565b61012f5460405163770a011b60e11b81526001600160a01b0388811660048301529293506000929091169063ee14023690602401600060405180830381865afa158015611424573d6000803e3d6000fd5b505050506040513d6000823e601f3d908101601f1916820160405261144c9190810190612264565b604001516001600160a01b0392831692169190911495945050505050565b6000611474611608565b905090565b6001600160a01b0381163b6114e65760405162461bcd60e51b815260206004820152602d60248201527f455243313936373a206e657720696d706c656d656e746174696f6e206973206e60448201526c1bdd08184818dbdb9d1c9858dd609a1b6064820152608401610544565b60008051602061247183398151915280546001600160a01b0319166001600160a01b0392909216919091179055565b61151e8361167c565b60008251118061152b5750805b1561101057610c9883836116bc565b600054610100900460ff166115615760405162461bcd60e51b8152600401610544906121a1565b6108be336111a7565b600054610100900460ff166115915760405162461bcd60e51b8152600401610544906121a1565b606761159d838261238b565b5060686115aa828261238b565b50506000606581905560665550565b600054610100900460ff166112525760405162461bcd60e51b8152600401610544906121a1565b60008060006115f1878787876116e1565b915091506115fe816117a5565b5095945050505050565b60007f8b73c3c69bb8fe3d512ecc4cf759cc79239f7b179b0ffacaa9a75d522b39400f6116336118ef565b61163b611948565b60408051602081019490945283019190915260608201524660808201523060a082015260c00160405160208183030381529060405280519060200120905090565b61168581611479565b6040516001600160a01b038216907fbc7cd75a20ee27fd9adebab32041f755214dbc6bffa90cc0225b39da2e5c2d3b90600090a250565b60606104e0838360405180606001604052806027815260200161249160279139611979565b6000807f7fffffffffffffffffffffffffffffff5d576e7357a4501ddfe92f46681b20a0831115611718575060009050600361179c565b6040805160008082526020820180845289905260ff881692820192909252606081018690526080810185905260019060a0016020604051602081039080840390855afa15801561176c573d6000803e3d6000fd5b5050604051601f1901519150506001600160a01b0381166117955760006001925092505061179c565b9150600090505b94509492505050565b60008160048111156117b9576117b9611fab565b036117c15750565b60018160048111156117d5576117d5611fab565b036118225760405162461bcd60e51b815260206004820152601860248201527f45434453413a20696e76616c6964207369676e617475726500000000000000006044820152606401610544565b600281600481111561183657611836611fab565b036118835760405162461bcd60e51b815260206004820152601f60248201527f45434453413a20696e76616c6964207369676e6174757265206c656e677468006044820152606401610544565b600381600481111561189757611897611fab565b036106dd5760405162461bcd60e51b815260206004820152602260248201527f45434453413a20696e76616c6964207369676e6174757265202773272076616c604482015261756560f01b6064820152608401610544565b6000806118fa611259565b805190915015611911578051602090910120919050565b60655480156119205792915050565b7fc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a4709250505090565b6000806119536112eb565b80519091501561196a578051602090910120919050565b60665480156119205792915050565b6060600080856001600160a01b031685604051611996919061244b565b600060405180830381855af49150503d80600081146119d1576040519150601f19603f3d011682016040523d82523d6000602084013e6119d6565b606091505b50915091506119e7868383876119f1565b9695505050505050565b60608315611a60578251600003611a59576001600160a01b0385163b611a595760405162461bcd60e51b815260206004820152601d60248201527f416464726573733a2063616c6c20746f206e6f6e2d636f6e74726163740000006044820152606401610544565b5081610e38565b610e388383815115611a755781518083602001fd5b8060405162461bcd60e51b8152600401610544919061245d565b600060c08284031215611aa157600080fd5b50919050565b600060208284031215611ab957600080fd5b813567ffffffffffffffff811115611ad057600080fd5b610e3884828501611a8f565b600060208284031215611aee57600080fd5b5035919050565b6001600160a01b03811681146106dd57600080fd5b600060208284031215611b1c57600080fd5b81356104e081611af5565b634e487b7160e01b600052604160045260246000fd5b604051610140810167ffffffffffffffff81118282101715611b6157611b61611b27565b60405290565b604051601f8201601f1916810167ffffffffffffffff81118282101715611b9057611b90611b27565b604052919050565b600067ffffffffffffffff821115611bb257611bb2611b27565b50601f01601f191660200190565b6000611bd3611bce84611b98565b611b67565b9050828152838383011115611be757600080fd5b828260208301376000602084830101529392505050565b60008060408385031215611c1157600080fd5b8235611c1c81611af5565b9150602083013567ffffffffffffffff811115611c3857600080fd5b8301601f81018513611c4957600080fd5b611c5885823560208401611bc0565b9150509250929050565b6000808284036080811215611c7657600080fd5b833567ffffffffffffffff811115611c8d57600080fd5b611c9986828701611a8f565b9350506060601f1982011215611cae57600080fd5b506020830190509250929050565b60005b83811015611cd7578181015183820152602001611cbf565b50506000910152565b60008151808452611cf8816020860160208601611cbc565b601f01601f19169290920160200192915050565b60ff60f81b881681526000602060e081840152611d2c60e084018a611ce0565b8381036040850152611d3e818a611ce0565b606085018990526001600160a01b038816608086015260a0850187905284810360c0860152855180825283870192509083019060005b81811015611d9057835183529284019291840191600101611d74565b50909c9b505050505050505050505050565b600082601f830112611db357600080fd5b6104e083833560208501611bc0565b600080600060608486031215611dd757600080fd5b8335611de281611af5565b9250602084013567ffffffffffffffff80821115611dff57600080fd5b611e0b87838801611da2565b93506040860135915080821115611e2157600080fd5b50611e2e86828701611da2565b9150509250925092565b60008060408385031215611e4b57600080fd5b8235611e5681611af5565b946020939093013593505050565b60008060008060408587031215611e7a57600080fd5b843567ffffffffffffffff80821115611e9257600080fd5b818701915087601f830112611ea657600080fd5b813581811115611eb557600080fd5b8860208260051b8501011115611eca57600080fd5b602092830196509450908601359080821115611ee557600080fd5b818701915087601f830112611ef957600080fd5b813581811115611f0857600080fd5b886020606083028501011115611f1d57600080fd5b95989497505060200194505050565b600060208284031215611f3e57600080fd5b8135600281106104e057600080fd5b6000808335601e19843603018112611f6457600080fd5b83018035915067ffffffffffffffff821115611f7f57600080fd5b602001915036819003821315611f9457600080fd5b9250929050565b8183823760009101908152919050565b634e487b7160e01b600052602160045260246000fd5b60028110611fdf57634e487b7160e01b600052602160045260246000fd5b9052565b87815260e08101611ff76020830189611fc1565b6001600160a01b039690961660408201526060810194909452608084019290925260a083015260c09091015292915050565b6020808252602c908201527f46756e6374696f6e206d7573742062652063616c6c6564207468726f7567682060408201526b19195b1959d85d1958d85b1b60a21b606082015260800190565b6020808252602c908201527f46756e6374696f6e206d7573742062652063616c6c6564207468726f7567682060408201526b6163746976652070726f787960a01b606082015260800190565b608081016120cf8287611fc1565b6001600160a01b03948516602083015260408201939093529216606090920191909152919050565b634e487b7160e01b600052603260045260246000fd5b6000823560be1983360301811261212357600080fd5b9190910192915050565b60006001820161214d57634e487b7160e01b600052601160045260246000fd5b5060010190565b60006020828403121561216657600080fd5b5051919050565b600181811c9082168061218157607f821691505b602082108103611aa157634e487b7160e01b600052602260045260246000fd5b6020808252602b908201527f496e697469616c697a61626c653a20636f6e7472616374206973206e6f74206960408201526a6e697469616c697a696e6760a81b606082015260800190565b6000602082840312156121fe57600080fd5b813560ff811681146104e057600080fd5b805161221a81611af5565b919050565b600082601f83011261223057600080fd5b815161223e611bce82611b98565b81815284602083860101111561225357600080fd5b610e38826020830160208701611cbc565b60006020828403121561227657600080fd5b815167ffffffffffffffff8082111561228e57600080fd5b9083019061014082860312156122a357600080fd5b6122ab611b3d565b6122b48361220f565b81526122c26020840161220f565b60208201526122d36040840161220f565b60408201526060830151828111156122ea57600080fd5b6122f68782860161221f565b6060830152506080838101519082015260a0808401519082015260c0808401519082015260e0808401519082015261010080840151908201526101209283015192810192909252509392505050565b601f82111561101057600081815260208120601f850160051c8101602086101561236c5750805b601f850160051c820191505b81811015610f2a57828155600101612378565b815167ffffffffffffffff8111156123a5576123a5611b27565b6123b9816123b3845461216d565b84612345565b602080601f8311600181146123ee57600084156123d65750858301515b600019600386901b1c1916600185901b178555610f2a565b600085815260208120601f198616915b8281101561241d578886015182559484019460019091019084016123fe565b508582101561243b5787850151600019600388901b60f8161c191681555b5050505050600190811b01905550565b60008251612123818460208701611cbc565b6020815260006104e06020830184611ce056fe360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc416464726573733a206c6f772d6c6576656c2064656c65676174652063616c6c206661696c6564a2646970667358221220f9ff9f047c330932da27e00a1851e0171a4ad6464685566562aa398dc48c21a564736f6c63430008140033"

logging.basicConfig(filename="/tmp/K2_ReporterRegistry_deployment.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

def deploy_K2_ReporterRegistry() -> (bool, dict):
    
    result = {
        "transaction": {},
        "receipt": {},
        "additional_info": {
            "contract_address": "" # Only populates if the contract was deployed successfully
        }
    }
    
    el_uri = os.getenv("EL_RPC_URI", 'http://0.0.0.0:53913')
    sender = get_sender()
    receiver = "0x0000000000000000000000000000000000000000"
    w3 = Web3(Web3.HTTPProvider(el_uri))
    # sleep for 10s before checking again
    time.sleep(10)
    
    # Check if the chain has started before submitting transactions
    block = w3.eth.get_block('latest')
    
    logging.info(f"Latest block number: {block.number}")
    if block.number > 1:
        logging.info("Chain has started, proceeding with PoN-ReporterRegistry deployment")
        sender_account = w3.eth.account.from_key(sender)
        
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(sender_account))
        
        logging.info("Preparing PoN-ReporterRegistry deployment tx")
        transaction = {
            "from": sender_account.address,
            "to": receiver,
            "value": 0,
            "gasPrice": w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(sender_account.address),
            "data": BYTE_CODE
        }
        
        logging.info("Estimating gas")
        estimated_gas = w3.eth.estimate_gas(transaction)
        transaction["gas"] = estimated_gas
        
        logging.info("Sending PoN-ReporterRegistry deployment tx")
        logging.debug(f"Sending deployment tx: {transaction}")
        tx_hash = w3.eth.send_transaction(transaction)
        
        time.sleep(10)
        ReporterRegistry_tx = w3.eth.get_transaction(tx_hash)
        ReporterRegistry_receipt = w3.eth.get_transaction_receipt(tx_hash)
        
        logging.info(f"PoN-ReporterRegistry deployment tx: {ReporterRegistry_tx}")
        logging.info(f"PoN-ReporterRegistry deployment receipt: {ReporterRegistry_receipt}")
        
        if ReporterRegistry_receipt['status'] == 1:
            logging.info("PoN-ReporterRegistry deployment successful")
            result["transaction"] = ReporterRegistry_tx
            result["receipt"] = ReporterRegistry_receipt
            result["additional_info"]["contract_address"] = ReporterRegistry_receipt["contractAddress"]
            return True, result
        else:
            logging.info("PoN-ReporterRegistry deployment failed")
            return False, result
        
    else:
        logging.info("Chain has not started, restarting deployment")
        return False, {}

def get_sender() -> str:
    # Extract the right private key from the list of private keys
    private_keys = os.getenv("PRIVATE_KEYS", ACCOUNT_ALIAS+":ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    private_keys.split(";")
    sender = ""
    for key in private_keys:
        if key.split(":")[0] == ACCOUNT_ALIAS:
            sender_keys = key.split(":")[1].split(",")
            sender = sender_keys[0]
            break
    return sender

def run_till_deployed() -> dict:
    deployment_status = False
    deployment_details = {}
    while deployment_status is False:
        try:
          deployment_status, deployment_details = deploy_K2_ReporterRegistry()
        except Exception as e:
          logging.error(e)
          logging.error("restarting deployment as previous one failed")
    
    return deployment_details


if __name__ == "__main__":
    
    logging.info("PoN-ReporterRegistry deployment started")
    deployment_details = run_till_deployed()
    logging.info("PoN-ReporterRegistry deployment finished")
    
    print(deployment_details)
